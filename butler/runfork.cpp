#include <thread>
#include <vector>
#include<iostream>
#include <string>
using namespace std;
void run_a_fork(string c)
{
  system(("python fork.py "+ c).c_str());

}

int main(int argc,char** argv)
{
  // // std::vector<std::thread> v;
  // // for(char i = 'a';i<='e';++i)
  // // {
  //     std::thread f1 (run_a_fork,'i');
  //     std::thread f2 (run_a_fork,'i');
  //     // v.push_back( f);
  // // }
  //   f1.join();
  //   f2.join();
  // // for(auto& e:v)
  // // {
  // //   e.join();
  // // }
  //   return 0;
  std::thread a (run_a_fork,"a");     // spawn new thread that calls foo()
  std::thread b (run_a_fork,"b");  // spawn new thread that calls bar(0)
  std::thread c (run_a_fork,"c");  // spawn new thread that calls bar(0)
  std::thread d (run_a_fork,"d");  // spawn new thread that calls bar(0)
  std::thread e (run_a_fork,"e");  // spawn new thread that calls bar(0)


  // synchronize threads:
  a.join();                // pauses until first finishes
  b.join();               // pauses until second finishes
  c.join();               // pauses until second finishes
  d.join();               // pauses until second finishes
  e.join();               // pauses until second finishes



  return 0;
}
